import { Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';
import { Websocket } from 'websocket-ts/lib';
import { ConnectionRequest } from '../models/connection-request';

@Component({
  selector: 'app-game-setup',
  templateUrl: './game-setup.component.html',
  styleUrls: ['./game-setup.component.css']
})
export class GameSetupComponent implements OnInit {
  
  @Input() api_access_token: string | undefined
  @Input() user: Player | undefined;
  @Input() ws_connection : Websocket | undefined
  @Output() connection_request: EventEmitter<ConnectionRequest> = new EventEmitter<ConnectionRequest>()

  constructor() {  }

  ngOnInit(): void {
  }

  join_as_player(session_joincode: string): void {
    const request_body: string = JSON.stringify({"action": "join", "session_id": session_joincode, "is_coordinator": false, "player_data": this.user!.id_jwt})
    this.connection_request.emit(new ConnectionRequest(request_body, false))
  }

  async on_create(): Promise<void> {
    let created_session_id: string = await this.create_session()
    const request_body: string = JSON.stringify({"action": "join", "session_id": created_session_id, "is_coordinator": true})
    this.connection_request.emit(new ConnectionRequest(request_body, true))
  }

  async create_session() : Promise<string> {
    const auth_token: string = this.api_access_token!
    const response_promise: any = await fetch(`${environment.rest_api_url}/session/`, {method: 'POST',
      headers: {'Authorization': auth_token}
    });
    let response = await response_promise.json()
    return response.session_id
  }

}
