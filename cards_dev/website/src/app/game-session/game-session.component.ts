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
  @Input() answer_cards: Array<string> | undefined
  
  constructor() { }

  ngOnInit(): void {
  }

  on_start(): void {
    const start_game_request = JSON.stringify({
      "action": "start",
      "session_id": this.session!.joinCode,
      "player_data": this.player_data!.id_jwt,
    })
    console.log(`Sending start game request: ${start_game_request}`)
    this.connection!.send(start_game_request)
  }

  on_card_select(card: string): void {
    // send card selection and block other selections
  }

}
