/**
 * GoogleSignInButton — wraps @react-oauth/google's useGoogleLogin hook.
 * Usage: <GoogleSignInButton onSuccess={fn} onError={fn} text="Sign in with Google" />
 * onSuccess receives the raw credential string (ID token).
 */
import { useGoogleLogin } from '@react-oauth/google';

export default function GoogleSignInButton({ onSuccess, onError, text = 'Continue with Google', disabled = false }) {
  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      // useGoogleLogin returns an access_token, not an ID token.
      // We need the ID token — use the implicit flow (credential response).
      // This component uses the credential (ID token) flow instead.
    },
    onError,
    flow: 'implicit',
  });

  return null; // placeholder — see GoogleCredentialButton below
}

/**
 * GoogleCredentialButton — uses the one-tap / credential response which gives an ID token directly.
 * This is what we actually render.
 */
import { GoogleLogin } from '@react-oauth/google';

export function GoogleCredentialButton({ onSuccess, onError, text = 'signin_with' }) {
  return (
    <div className="flex justify-center">
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          onSuccess(credentialResponse.credential);
        }}
        onError={onError}
        text={text}
        shape="rectangular"
        size="large"
        width="340"
        logo_alignment="left"
        useOneTap={false}
      />
    </div>
  );
}
