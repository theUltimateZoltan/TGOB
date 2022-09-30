import { Component, Input, OnInit} from '@angular/core';
import fetch, { Headers } from 'node-fetch';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-game-setup',
  templateUrl: './game-setup.component.html',
  styleUrls: ['./game-setup.component.css']
})
export class GameSetupComponent implements OnInit {
  
  @Input()
  api_access_jwt: Map<string, string> = new Map([
    ["access_token", "invalid_token"]
  ])

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
      const auth_token: string = this.api_access_jwt.get("id_token")!
      const response = await fetch(`${environment.backend_api_url}/session/`, {method: 'POST', body: '{"creator_id": "front_end_user"}',
        headers: {'Authorization': auth_token}
      });
      const data = await response.json();
      console.log(data);
    
    
    return ""
  }

}
