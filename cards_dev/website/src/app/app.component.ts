import { Component } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Websocket, WebsocketBuilder } from 'websocket-ts/lib';
import { ConnectionRequest } from './models/connection-request';
import { GameSession } from './models/game-session';
import { Player } from './models/player';
import { Round } from './models/round';
import jwt_decode from 'jwt-decode';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'cards_fe';
  session : GameSession | undefined;
  is_coordinator: boolean | undefined
  api_access_jwt: Map<string, string> | undefined
  ws_connection: Websocket | undefined
  answer_cards_hand: Array<string> | undefined

  on_connection_requested(session_join_request: ConnectionRequest) {
    this.is_coordinator = session_join_request.is_coordinator
    this.open_websocket_connection(session_join_request.body)
  }

  open_websocket_connection(session_join_request: string): void {
    this.ws_connection = new WebsocketBuilder(environment.websocket_api_url)
      .onOpen((i, ev) => { 
        this.send_session_join_request(session_join_request) 
      })
      .onClose((i, ev) => { console.log("Disconnected from game api.") })
      .onError((i, ev) => { console.log("Game api connection error.") })
      .onMessage((i, ev) => { 
        const response_object: any = JSON.parse(ev.data)
        const response_body = JSON.parse(response_object.body)
        switch (response_object.directive) {
          case "update_session":
            console.log(`Updating session from response: ${response_object.body}`)
            this.session = new GameSession(response_body)
            break;
          case "update_round":
            console.log(`Updating round from response: ${response_object.body}`)
            this.session = new GameSession(response_body.session)
            this.session!.round = new Round(response_body.round)
            if (response_body.acards) {
              this.answer_cards_hand = response_body.acards.map((card: { text: string })=>card.text)
            }
            break;
          case "update_enrollment":
            console.log(`Updating session enrollment from response: ${response_object.body}`)
            this.session!.players.push(new Player(response_body.email, response_body.name))
            break;
          case "end_round":
            console.log(`Round finished with response: ${response_object.body}`)
            this.session!.players.push(new Player(response_body.email, response_body.name))
            this.session = new GameSession(response_body.session)
            this.session!.round = new Round(response_body.round)
            break;
          case "show_error":
            console.log(`Error: ${response_body.message}`)
            // show a pretty and dismissable error message
            break;
        }
      })
      .onRetry((i, ev) => { console.log("Connection retry...") })
      .build();
  }

  send_session_join_request(request_body: string): void {
    console.log(`sending join request: ${request_body}`)
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
      const user_details: any = jwt_decode(id_token)
      return new Player(user_details.email, user_details.name)
    }
    return undefined
  }

  get_session_stringified(): string {
    return JSON.stringify(this.session)
  }

  get_logged_in_user_stringified(): string {
    return JSON.stringify(this.get_logged_in_user())
  }
}