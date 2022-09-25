import { Component, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-game-setup',
  templateUrl: './game-setup.component.html',
  styleUrls: ['./game-setup.component.css']
})
export class GameSetupComponent implements OnInit {
  constructor() { }

  is_prod: boolean = environment.production

  ngOnInit(): void {
  }

  on_join(guid_input: string): void {
    console.log("attempt join: "+ guid_input)
  }

  on_create(): void {
    // invoke create and receive guid
    // subscribe to topic with filter on this game
    console.log(this.create_session())
    
  }

  private create_random_game_guid() : string {
    return Math.random().toString(36).substring(2,10);
  }

  async create_session() : Promise<string> {
    const response = await fetch(`${environment.backend_api_url}/session/`, {method: 'POST', body: '{"creator_id": "front_end_user"}'});
    const data = await response.json();
    console.log(data);
    return ""
  }

}
