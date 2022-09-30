import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-game-session',
  templateUrl: './game-session.component.html',
  styleUrls: ['./game-session.component.css']
})
export class GameSessionComponent implements OnInit {

  @Input() session_guid: string = "";
  
  @Input()
  api_access_jwt: Map<string, string> = new Map([
    ["access_token", "invalid_token"]
  ])

  is_coordinator: boolean = true;
  
  constructor() { }

  ngOnInit(): void {
  }

}
