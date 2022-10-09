import { Component, Input, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';
import { AWSError, CognitoIdentityCredentials, Endpoint, SNS } from 'aws-sdk';
import { config } from 'aws-sdk/index';
import { PromiseResult } from 'aws-sdk/lib/request';
import { WebsocketBuilder } from 'websocket-ts/lib';

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
    console.log(this.create_session())
    // connect to game via websocket api
    const ws = new WebsocketBuilder(environment.websocket_api_url)
      .onOpen((i, ev) => { console.log("Success connecting to game api.") })
      .onClose((i, ev) => { console.log("Disconnected from game api.") })
      .onError((i, ev) => { console.log("Game api connection error.") })
      .onMessage((i, ev) => { console.log("message") })
      .onRetry((i, ev) => { console.log("Connection retry...") })
      .build();
    // display coordinator graphics
  }

  async create_session() : Promise<string> {
    const auth_token: string = this.api_access_token!
    const response = await fetch(`${environment.rest_api_url}/session/`, {method: 'POST', body: JSON.stringify({"creator_id": this.user!.email}),
      headers: {'Authorization': auth_token}
    });
    return await response.json();
  }

}
