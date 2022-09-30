import { Component, Input, OnInit} from '@angular/core';
import fetch from 'node-fetch';
import { environment } from 'src/environments/environment';
import { Player } from '../models/player';

@Component({
  selector: 'app-game-setup',
  templateUrl: './game-setup.component.html',
  styleUrls: ['./game-setup.component.css']
})
export class GameSetupComponent implements OnInit {
  
  @Input()
  api_access_token: string | undefined

  @Input()
  user: Player | undefined;

  constructor() {  }

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

  async create_session() : Promise<string> {
      const auth_token: string = this.api_access_token!
      const response = await fetch(`${environment.backend_api_url}/session/`, {method: 'POST', body: JSON.stringify({"creator_id": this.user!.email}),
        headers: {'Authorization': auth_token}
      });
      const data = await response.json();
      console.log(data);
    
    
    return ""
  }

}
