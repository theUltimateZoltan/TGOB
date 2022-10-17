import { Component, Input, OnInit } from '@angular/core';
import { GameSession } from 'src/app/models/game-session';
import { Player } from 'src/app/models/player';
import { Websocket } from 'websocket-ts/lib';

@Component({
  selector: 'app-arbiter',
  templateUrl: './arbiter.component.html',
  styleUrls: ['./arbiter.component.css']
})
export class ArbiterComponent implements OnInit {
  @Input() session: GameSession | undefined
  @Input() connection: Websocket | undefined
  @Input() player_data: Player | undefined

  constructor() { }

  ngOnInit(): void {
  }

  on_arbitration(answer: string): void {
    const arbitration_request = JSON.stringify({
      "action": "arbitrate",
      "session_id": this.session!.joinCode,
      "player_data": {"email":this.player_data!.email, "username": this.player_data!.name},
      "arbitration": answer
    })
    console.log(`Sending arbitration request: ${arbitration_request}`)
    this.connection!.send(arbitration_request)
  }

}
