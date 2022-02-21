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
from typing import Optional

import aiounittest

from tchap_displayname_email import AUTH_TYPE_EMAIL, TchapDisplaynameEmail
from tests import create_module


class DisplaynameTestCase(aiounittest.AsyncTestCase):
    async def test_no_email(self) -> None:
        """Tests that the module returns None if there's no email provided."""
        module = create_module()
        res = await module.extract_displayname_from_email({}, {})
        self.assertIsNone(res)

    async def test_matrix_org(self) -> None:
        """Tests that the module returns the correct org if a matrix.org email is
        provided.
        """
        module = create_module()
        res = await self._get_displayname(module, "foo.bar@matrix.org")
        self.assertEqual(res, "Foo Bar [Tchap Admin]")

    async def test_gouv_fr(self) -> None:
        """Tests that the module returns the correct org if a gouv.fr (without subdomain)
        email is provided.
        """
        module = create_module()
        res = await self._get_displayname(module, "foo.bar@gouv.fr")
        self.assertEqual(res, "Foo Bar [Gouv]")

    async def test_gouv_fr_sub(self) -> None:
        """Tests that the module returns the correct org if a gouv.fr (with subdomain)
        email is provided.
        """
        module = create_module()
        res = await self._get_displayname(module, "foo.bar@education.gouv.fr")
        self.assertEqual(res, "Foo Bar [Education]")

    async def test_other_domain(self) -> None:
        """Tests that the module returns the correct org if an email of a unknown domain
        is provided.
        """
        module = create_module()
        res = await self._get_displayname(module, "foo.bar@nikan.com")
        self.assertEqual(res, "Foo Bar [Nikan]")

    async def test_hyphen(self) -> None:
        """Tests that the module capitalises name parts even if they're only separated by
        a hyphen.
        """
        module = create_module()
        res = await self._get_displayname(module, "foo-bar.baz@nikan.com")
        self.assertEqual(res, "Foo-Bar Baz [Nikan]")

    async def test_no_last_name(self) -> None:
        """Tests that the module doesn't always expect a last name to be provided."""
        module = create_module()
        res = await self._get_displayname(module, "foo@nikan.com")
        self.assertEqual(res, "Foo [Nikan]")

    async def test_not_extract(self) -> None:
        """Tests that the module returns directly with the provided email address if told
        to do so.
        """
        module = create_module({"extract_from_email": False})
        res = await self._get_displayname(module, "foo@nikan.com")
        self.assertEqual(res, "foo@nikan.com")

    async def _get_displayname(
        self,
        module: TchapDisplaynameEmail,
        email: Optional[str],
    ) -> Optional[str]:
        """Calls the extract_displayname_from_email method on the given module using the
        given email address.
        """
        results = {}
        if email is not None:
            results[AUTH_TYPE_EMAIL] = {"address": email}

        return await module.extract_displayname_from_email(results, {})
