import { Component, Input, OnInit } from '@angular/core';
import { GameSession } from '../models/game-session';

@Component({
  selector: 'app-game-session',
  templateUrl: './game-session.component.html',
  styleUrls: ['./game-session.component.css']
})
export class GameSessionComponent implements OnInit {

  @Input() session: GameSession | undefined;
  
  @Input()
  api_access_token: string | undefined

  is_coordinator: boolean = true;
  
  constructor() { }

  ngOnInit(): void {
  }

}
