import { Component } from '@angular/core';
import jwt_decode from 'jwt-decode';
import { environment } from 'src/environments/environment';
import { Websocket, WebsocketBuilder } from 'websocket-ts/lib';
import { GameSession } from './models/game-session';
import { Player } from './models/player';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'cards_fe';
  session : GameSession | undefined;

  api_access_jwt: Map<string, string> | null = null

  ws_connection: Websocket | undefined

  on_connection_requested(session_join_request: string) {
    this.open_websocket_connection(session_join_request)
  }

  open_websocket_connection(session_join_request: string): void {
    this.ws_connection = new WebsocketBuilder(environment.websocket_api_url)
      .onOpen((i, ev) => { 
        this.send_websocket_request(session_join_request) 
      })
      .onClose((i, ev) => { console.log("Disconnected from game api.") })
      .onError((i, ev) => { console.log("Game api connection error.") })
      .onMessage((i, ev) => { 
        const response_object: any = JSON.parse(ev.data)
        this.session = new GameSession(JSON.parse(response_object.body))
      })
      .onRetry((i, ev) => { console.log("Connection retry...") })
      .build();
  }

  send_websocket_request(request_body: string): void {
    console.log(`sending websocket request: ${request_body}`)
    this.ws_connection!.send(request_body)
    console.log(`Join request sent.`)
  }

  on_login(token: Map<string, string>) {
    this.api_access_jwt = token
    window.localStorage.setItem("api_token", this.api_access_jwt.get("id_token") ?? "")
  }

  get_api_access_token(): string {
    return window.localStorage.getItem("api_token") ?? ""
  }

  get_logged_in_user(): Player | undefined {
    let id_token: string = this.get_api_access_token()
    if (id_token) {
      let user_details: any = jwt_decode(id_token)
      return new Player(user_details.email, user_details.name, id_token)
    }
    return undefined
  }
}