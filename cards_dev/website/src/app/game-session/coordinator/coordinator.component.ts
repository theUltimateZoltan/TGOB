import { Component, Input, OnInit } from '@angular/core';
import { GameSession } from 'src/app/models/game-session';
import { QuestionCard } from "../../models/question-card";

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

  get_next_question_card(): QuestionCard {
    return new QuestionCard("1234")
  } 

}
