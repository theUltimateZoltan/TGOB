import aws_cdk as core
import aws_cdk.assertions as assertions

from cards_infra_dev.cards_dev.backend import CardsInfraDevStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cards_infra_dev/cards_infra_dev_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CardsInfraDevStack(app, "cards-infra-dev")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

    template.has_resource_properties("AWS::SNS::Topic", {
        "TopicName": "CardsEventNotifier"
    })
