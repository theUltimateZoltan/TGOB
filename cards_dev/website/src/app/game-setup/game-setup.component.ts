import { Component, Input, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';
import { AWSError, CognitoIdentityCredentials, Endpoint, SNS } from 'aws-sdk';
import { config } from 'aws-sdk/index';
import { PromiseResult } from 'aws-sdk/lib/request';
import { WebsocketBuilder, Websocket } from 'websocket-ts/lib';
import { GameSession } from '../models/game-session';

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

  ws_connection: Websocket | undefined 

  constructor() {  }

  ngOnInit(): void {
  }

  on_join(guid_input: string): void {
    console.log("attempt join: "+ guid_input)
  }

  join_as_coordinator(session: GameSession): void {
    console.log(`sending join request for ${session.joinCode}...`)
    this.ws_connection!.send(JSON.stringify({"action": "join", "session_id": session.joinCode, "is_coordinator": true}))
    console.log(`Join request sent: ${JSON.stringify({"action": "join", "session_id": session.joinCode, "is_coordinator": true})}`)
  }

  async on_create(): Promise<void> {
    let created_session: GameSession = await this.create_session()

    // connect to game via websocket api
    this.ws_connection = new WebsocketBuilder(environment.websocket_api_url)
      .onOpen((i, ev) => { this.join_as_coordinator(created_session) })
      .onClose((i, ev) => { console.log("Disconnected from game api.") })
      .onError((i, ev) => { console.log("Game api connection error.") })
      .onMessage((i, ev) => { console.log(ev.data) })
      .onRetry((i, ev) => { console.log("Connection retry...") })
      .build();
    

    // display coordinator graphics
  }

  async create_session() : Promise<GameSession> {
    const auth_token: string = this.api_access_token!
    const response = await fetch(`${environment.rest_api_url}/session/`, {method: 'POST',
      headers: {'Authorization': auth_token}
    });
    let response_json = await response.json()
    let created_session: GameSession = new GameSession(response_json)

    return created_session;
  }

}
