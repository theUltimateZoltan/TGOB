import { Component, Input, OnInit } from '@angular/core';
import { Websocket } from 'websocket-ts/lib';
import { GameSession } from '../models/game-session';
import { Player } from '../models/player';

@Component({
  selector: 'app-game-session',
  templateUrl: './game-session.component.html',
  styleUrls: ['./game-session.component.css']
})
export class GameSessionComponent implements OnInit {

  @Input() session: GameSession | undefined
  @Input() is_coordinator: boolean | undefined
  @Input() connection: Websocket | undefined
  @Input() player_data: Player | undefined
  
  constructor() { }

  ngOnInit(): void {
  }

  on_start() {
    const start_game_request = JSON.stringify({
      "session_id": this.session!.joinCode,
      "player_data": this.player_data!.id_jwt,
    })
    this.connection!.send(start_game_request)
  }

}
