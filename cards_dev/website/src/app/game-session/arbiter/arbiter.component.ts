import { Component, Input, OnInit } from '@angular/core';
import { GameSession } from 'src/app/models/game-session';

@Component({
  selector: 'app-arbiter',
  templateUrl: './arbiter.component.html',
  styleUrls: ['./arbiter.component.css']
})
export class ArbiterComponent implements OnInit {
  @Input() session: GameSession | undefined

  constructor() { }

  ngOnInit(): void {
  }

  on_arbitration(answer: string): void {
    console.log(`arbitrated in favor of ${answer}`)
    // send arbitration (still needs lambda)
  }

}
