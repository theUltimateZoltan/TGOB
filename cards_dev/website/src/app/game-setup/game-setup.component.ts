import { Component, Input, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';
import { AWSError, CognitoIdentityCredentials, Endpoint, SNS } from 'aws-sdk';
import { config } from 'aws-sdk/index';
import { PromiseResult } from 'aws-sdk/lib/request';

@Component({
  selector: 'app-game-setup',
  templateUrl: './game-setup.component.html',
  styleUrls: ['./game-setup.component.css']
})
export class GameSetupComponent implements OnInit {
  
  @Input()
  api_access_token: string | undefined

  @Input()
  user: Player | undefined;

  constructor() {  }

  ngOnInit(): void {
  }

  on_join(guid_input: string): void {
    console.log("attempt join: "+ guid_input)
  }

  on_create(): void {
    // invoke create and receive guid
    // subscribe to topic with filter on this game
    console.log(this.create_session())
    
  }

  async create_session() : Promise<string> {
    const auth_token: string = this.api_access_token!
    const response = await fetch(`${environment.backend_api_url}/session/`, {method: 'POST', body: JSON.stringify({"creator_id": this.user!.email}),
      headers: {'Authorization': auth_token}
    });
    const data = await response.json();
    console.log(data);

    var params = { 
      Protocol: 'application',
      TopicArn : environment.progress_notifier_arn,
      Attributes:{ 
        FilterPolicy : `{"session_id": "${ data.session_id }"}`
      }
     // Endpoint: ftsio
    }

    var myCredentials = new CognitoIdentityCredentials({
      IdentityPoolId: environment.cognito_identity_pool_id,
      Logins: {
        "cognito-idp.us-west-2.amazonaws.com/us-west-2_zd1xUQuZy" : this.api_access_token!
      }
    });
    config.update({
      credentials: myCredentials, region: 'us-west-2'
    });
    console.log(config)
    var progress_notified = new SNS({apiVersion: '2010-03-31', credentials: config.credentials}).subscribe(params).promise()
    progress_notified.then(this.game_progress_notified_handler)
      
    return ""
  }

  game_progress_notified_handler(event: PromiseResult<SNS.SubscribeResponse, AWSError>): any {
    console.log(event.SubscriptionArn)
  }

}
