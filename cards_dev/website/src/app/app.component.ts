import { Component } from '@angular/core';
import jwt_decode from 'jwt-decode';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'cards_fe';
  session_guid = null;

  api_access_jwt: Map<string, string> | null = null
  user_details: any = null

  onLogin(token: Map<string, string>) {
    this.api_access_jwt = token
    this.user_details = jwt_decode(this.api_access_jwt.get("id_token")!)
  }
}