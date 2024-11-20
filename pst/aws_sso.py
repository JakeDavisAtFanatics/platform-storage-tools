import boto3  # type: ignore
import subprocess
from botocore.exceptions import ClientError, UnauthorizedSSOTokenError  # type: ignore


class AwsSsoService:
    def __init__(self):
        self.session = None

    def authenticate(self, profile_name: str):
        if self._is_authenticated(profile_name):
            return

        try:
            self.session = boto3.Session(profile_name=profile_name)
            sts = self.session.client("sts")
            sts.get_caller_identity()
        except (ClientError, UnauthorizedSSOTokenError) as e:
            if isinstance(
                e, UnauthorizedSSOTokenError
            ) or "UnauthorizedException" in str(e):
                print(f"SSO token is expired or invalid for profile: {profile_name}")
                self._refresh_sso_login(profile_name)
                self.authenticate(profile_name)  # Retry authentication after refresh
            else:
                print(f"Failed to authenticate with AWS SSO: {e}")
                raise

    def get_session(self):
        if not self.session:
            raise Exception("Not authenticated. Call authenticate() first.")
        return self.session

    def _is_authenticated(self, profile_name: str):
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client("sts")
            sts.get_caller_identity()
            self.session = session
            return True
        except:  # noqa: E722
            return False

    def _refresh_sso_login(self, profile_name: str):
        print(f"Refreshing SSO login for profile: {profile_name}")
        try:
            subprocess.run(
                ["aws", "sso", "login", "--profile", profile_name], check=True
            )
            print("SSO login refreshed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to refresh SSO login: {e}")
            raise
