import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {

  @Output()
  api_access_jwt: EventEmitter<Map<string, string>> = new EventEmitter<Map<string, string>>()

  @Input()
  user_name: string | undefined = undefined

  auth_url: string = "https://auth.devcards.eladlevy.click/login?"
  cognito_client_id: string = environment.cognito_user_pool_client_id
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

  cognitoHostedUiCallbackHandler() {
    if(window.location.hash && window.location.hash.indexOf("id_token") > 0) {
      let jwt = window.location.hash.replace("#", "").split("&").reduce(function(map, pair) {
        map.set(pair.split("=")[0], pair.split("=")[1])
        return map
      }, new Map())

      this.api_access_jwt.emit(jwt)
      window.location.href = window.location.href.split("#")[0]
    }
  }

  constructor() { }

  ngOnInit(): void {
    this.cognitoHostedUiCallbackHandler()
  }
}
