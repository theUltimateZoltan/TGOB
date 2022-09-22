import { Component, Input, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { QuestionCard } from "../../models/question-card";

@Component({
  selector: 'app-coordinator',
  templateUrl: './coordinator.component.html',
  styleUrls: ['./coordinator.component.css']
})
export class CoordinatorComponent implements OnInit {

  @Input() session_guid: string = "";

  constructor() { }

  ngOnInit(): void {
  }

  get_next_question_card(): QuestionCard {
    return new QuestionCard("1234")
  } 

}
