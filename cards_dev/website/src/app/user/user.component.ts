import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {

  auth_url: string = "https://auth.devcards.eladlevy.click/login?"
  cognito_client_id: string = environment.cognito_client_id
  response_type: string = "token"
  scope: string = "aws.cognito.signin.user.admin+email+openid+phone+profile"
  redirect_uri: string = encodeURIComponent("https://devcards.eladlevy.click")

  get_login_url() {
    let uri: string = `${this.auth_url}
    client_id=${this.cognito_client_id}&
    response_type=${this.response_type}&
    scope=${this.scope}&
    redirect_uri=${this.redirect_uri}
    `.replace(/\s/g, "")
    return uri
  }

  get_signup_url() {
    return this.get_login_url().replace("login?", "signup?")
  }

  constructor() { }

  ngOnInit(): void {
  }

}
