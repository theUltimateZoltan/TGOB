import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'cards_fe';
  session_guid = null;

  api_access_jwt: Map<string, string> | null = null
  user_logged_in = false

  onLogin(token: Map<string, string>) {
    this.api_access_jwt = token
    this.user_logged_in = true
  }
}
