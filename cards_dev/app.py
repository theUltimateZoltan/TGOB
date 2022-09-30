#!/usr/bin/env python3
import os

import aws_cdk as cdk
from cards_dev.back_end import CardsBackend

from cards_dev.endpoints import CardsEndpoints
from cards_dev.front_end import CardsFrontEnd
from cards_dev.game_data import CardsGameData
from cards_dev.user_data import CardsUserData

app = cdk.App()
aws_environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

endpoints_stack = CardsEndpoints(app, "Endpoints", env=aws_environment)
user_data_stack = CardsUserData(app, "UserData", env=aws_environment, endpoints_stack=endpoints_stack)
backend_stack = CardsBackend(app, "Backend", env=aws_environment, endpoints_stack=endpoints_stack, user_data_stack=user_data_stack)
CardsFrontEnd(app, "Frontend", env=aws_environment, endpoints_stack=endpoints_stack)
CardsGameData(app, "GameData", env=aws_environment, backend_stack=backend_stack)

app.synth()
