#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cards_dev.back_end import CardsBackend
from cards_dev.user_data import CardsDataBase
from cards_dev.front_end import CardsFrontEnd

app = cdk.App()
aws_environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

backend_stack = CardsBackend(app, "CardsBackEnd", env=aws_environment)
frontend_stack = CardsFrontEnd(app, "CardsFrontEnd", endpoints_stack=backend_stack, env=aws_environment)
databse_stack = CardsDataBase(app, "CardsDataBase", backend=backend_stack, env=aws_environment)

databse_stack.add_dependency(frontend_stack)  # cognito user pool subdomain requires a defined environment domain

app.synth()
