import { Component } from '@angular/core';
import jwt_decode from 'jwt-decode';
import { Player } from './models/player';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'cards_fe';
  session_guid = null;

  api_access_jwt: Map<string, string> | null = null

  onLogin(token: Map<string, string>) {
    this.api_access_jwt = token
    window.localStorage.setItem("api_token", this.api_access_jwt.get("id_token") ?? "")
  }

  getApiAccessToken(): string {
    return window.localStorage.getItem("api_token") ?? ""
  }

  getLoggedInUser(): Player | undefined {
    let id_token: string = this.getApiAccessToken()
    if (id_token) {
      let user_details: any = jwt_decode(id_token)
      return new Player(user_details.email, user_details.name, id_token)
    }
    return undefined
  }
}