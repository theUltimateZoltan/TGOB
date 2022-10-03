// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  production: false,
  backend_api_url: "https://bu72lka3ik.execute-api.us-west-2.amazonaws.com/prod",
  website_url: "localhost:4200",
  cognito_user_pool_client_id: "4k9ppkrbhj153128nbr282q6p3",
  cognito_user_pool_id: "us-west-2_zd1xUQuZy",
  cognito_identity_pool_id: "us-west-2:8f801c2c-eb92-44cd-a16d-1aac951ea59e",
  aws_region: "us-west-2",
  progress_notifier_arn : "arn:aws:sns:us-west-2:451230547744:dev_game_progress_notifier"

};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
