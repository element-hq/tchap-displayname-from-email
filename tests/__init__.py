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
from unittest.mock import Mock

from synapse.module_api import ModuleApi

from tchap_username_email import TchapUsernameEmail


def create_module(raw_config: Optional[Dict[str, Any]] = None) -> TchapUsernameEmail:
    # Create a mock based on the ModuleApi spec, but override some mocked functions
    # because some capabilities are needed for running the tests.
    module_api = Mock(spec=ModuleApi)

    # Give parse_config some configuration to parse.
    if raw_config is None:
        raw_config = {}

    config = TchapUsernameEmail.parse_config(raw_config)

    return TchapUsernameEmail(config, module_api)
