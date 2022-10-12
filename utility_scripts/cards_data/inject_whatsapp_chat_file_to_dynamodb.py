import math
from typing import Union
import random
from typing import List
import re
import boto3

QUESTION_MARK = "❓"
ANSWER_MARK = "❗"
BLANK = "_"

def convert_line(line: str) -> Union[dict, None]:
    if QUESTION_MARK in line:
        content = line.split(QUESTION_MARK)[1]
        content = re.sub("_+", "{$}", content)
        type = "Q"
    elif ANSWER_MARK in line:
        content = line.split(ANSWER_MARK)[1]
        type = "A"
    else:
        return None

    return {
        "text": content.strip(), 
        "type": type, 
        "distributions": 
                {
                    "uniform": str(random.uniform(0.0, 1.0))
                }
            }

def main() -> None:
    card_dicts: List[dict] = list()
    with open("chat_export.txt", "r") as chat_export_file:
        while (line:=chat_export_file.readline()):
            if converted:=convert_line(line):
                card_dicts.append(converted)
    with open("cards_data.json", "w") as json_cards_list:
        json_cards_list.write(repr(card_dicts))
    print("Converted whatsapp chat to JSON objects. See the exported file.")
    upload_to_dynamodb(card_dicts)
    print("Converted uploaded cards to dynamoDB as JSON objects.")

    

def upload_to_dynamodb(json_cards_list: List[dict]):
    dynamodb_client = boto3.client("dynamodb")
    
    for i in range(0, (math.ceil(len(json_cards_list)/25)), 25):
        dynamodb_client.batch_write_item(RequestItems={
                "dev_cards_data": [
                    {
                        "PutRequest": {
                            "Item" : {
                                "text": {"S": card.get("text")},
                                "type": {"S": card.get("type")},
                                "distributions": {"M": {
                                    "uniform": {"N" : card.get("distributions").get("uniform")}
                                    }
                                }
                            }
                        }
                    }
                    for card in json_cards_list[i: i+25]
                ]
            }
    )

if __name__ == "__main__":
    main()