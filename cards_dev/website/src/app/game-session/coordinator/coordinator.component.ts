import { Component, Input, OnInit } from '@angular/core';
import { GameSession } from 'src/app/models/game-session';

@Component({
  selector: 'app-coordinator',
  templateUrl: './coordinator.component.html',
  styleUrls: ['./coordinator.component.css']
})
export class CoordinatorComponent implements OnInit {

  @Input() session: GameSession | undefined

  constructor() { }

  ngOnInit(): void {

  }

}
