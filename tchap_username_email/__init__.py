# Copyright 2022 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, Optional

import attr
from synapse.module_api import ModuleApi

AUTH_TYPE_EMAIL = "m.login.email.identity"


@attr.s(auto_attribs=True, frozen=True)
class TchapUsernameEmailConfig:
    extract_from_email: bool


class TchapUsernameEmail:
    def __init__(self, config: TchapUsernameEmailConfig, api: ModuleApi):
        # Keep a reference to the config.
        self._config = config

        api.register_password_auth_provider_callbacks(
            get_display_name_for_registration=self.extract_displayname_from_email,
        )

    @staticmethod
    def parse_config(config: Dict[str, Any]) -> TchapUsernameEmailConfig:
        extract_from_email = config.get("extract_from_email", True)
        return TchapUsernameEmailConfig(
            extract_from_email=extract_from_email,
        )

    async def extract_displayname_from_email(
        self,
        uia_results: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Optional[str]:
        """Checks if an email address can be found in the UIA results, and if so derives
        the display name from it.

        Args:
            uia_results: The UIA results.
            params: The parameters of the registration request.

        Returns:
            The username if an email address could be found in the UIA results, None
            otherwise. If an email is present, and `extract_from_email` is True, then
            the email address is used as is.
        """
        if AUTH_TYPE_EMAIL in uia_results:
            address: str = uia_results[AUTH_TYPE_EMAIL]["address"]

            if self._config.extract_from_email:
                return _map_email_to_displayname(address)

            return address

        return None


def cap(name: str) -> str:
    """Capitalise parts of a name containing different words, including those
    separated by hyphens.

    For example, 'John-Doe'

    Args:
        The name to parse
    """
    if not name:
        return name

    # Split the name by whitespace then hyphens, capitalizing each part then
    # joining it back together.
    capitalized_name = " ".join(
        "-".join(part.capitalize() for part in space_part.split("-"))
        for space_part in name.split()
    )
    return capitalized_name


def _map_email_to_displayname(address: str) -> str:
    """Custom mapping from an email address to a user displayname

    Args:
        address: The email address to process

    Returns:
        The new displayname
    """
    # Split the part before and after the @ in the email.
    # Replace all . with spaces in the first part
    parts = address.replace(".", " ").split("@")

    # Figure out which org this email address belongs to
    org_parts = parts[1].split(" ")

    # If this is a ...matrix.org email, mark them as an Admin
    if org_parts[-2] == "matrix" and org_parts[-1] == "org":
        org = "Tchap Admin"

    # Is this is a ...gouv.fr address, set the org to whatever is before
    # gouv.fr. If there isn't anything (a @gouv.fr email) simply mark their
    # org as "gouv"
    elif org_parts[-2] == "gouv" and org_parts[-1] == "fr":
        org = org_parts[-3] if len(org_parts) > 2 else org_parts[-2]

    # Otherwise, mark their org as the email's second-level domain name
    else:
        org = org_parts[-2]

    desired_display_name = cap(parts[0]) + " [" + cap(org) + "]"

    return desired_display_name
