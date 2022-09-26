#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cards_dev.backend import CardsBackend
from cards_dev.database import CardsDataBase
from cards_dev.s3_angular_website import CardsFrontEnd

app = cdk.App()
aws_environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

backend_stack = CardsBackend(app, "CardsBackEnd", env=aws_environment)
frontend_stack = CardsFrontEnd(app, "CardsFrontEnd", backend=backend_stack, env=aws_environment)
databse_stack = CardsDataBase(app, "CardsDataBase", backend=backend_stack, env=aws_environment)

databse_stack.add_dependency(frontend_stack)  # cognito user pool subdomain requires a defined environment domain

app.synth()
