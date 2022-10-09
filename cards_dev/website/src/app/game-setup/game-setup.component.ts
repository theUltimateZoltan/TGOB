import { Component, Input, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';
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

  open_websocket_connection(session_join_request: string): void {
    this.ws_connection = new WebsocketBuilder(environment.websocket_api_url)
      .onOpen((i, ev) => { this.send_websocket_request(session_join_request) })
      .onClose((i, ev) => { console.log("Disconnected from game api.") })
      .onError((i, ev) => { console.log("Game api connection error.") })
      .onMessage((i, ev) => { console.log(ev.data) })
      .onRetry((i, ev) => { console.log("Connection retry...") })
      .build();
  }

  send_websocket_request(request_body: string): void {
    console.log(`sending websocket request: ${request_body}`)
    this.ws_connection!.send(request_body)
    console.log(`Join request sent.`)
  }

  join_as_player(session_joincode: string): void {
    const request_body: string = JSON.stringify({"action": "join", "session_id": session_joincode, "is_coordinator": false, "player_data": this.user!.id_jwt})
    this.open_websocket_connection(request_body)
  }

  async on_create(): Promise<void> {
    let created_session: GameSession = await this.create_session()
    const request_body: string = JSON.stringify({"action": "join", "session_id": created_session.joinCode, "is_coordinator": true})
    this.open_websocket_connection(request_body)
  }

  async create_session() : Promise<GameSession> {
    const auth_token: string = this.api_access_token!
    const response = await fetch(`${environment.rest_api_url}/session/`, {method: 'POST',
      headers: {'Authorization': auth_token}
    });
    let created_session: GameSession = new GameSession(await response.json())
    return created_session;
  }

}
