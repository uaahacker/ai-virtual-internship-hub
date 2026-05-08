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

export function GoogleCredentialButton({ onSuccess, onError, text = 'signin_with', loading = false }) {
  return (
    <div className="flex flex-col items-center gap-2">
      {/* Hide the Google button visually when loading but keep it mounted */}
      <div className={loading ? 'pointer-events-none opacity-0 h-0 overflow-hidden' : ''}>
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

      {loading && (
        <div className="flex items-center justify-center gap-3 w-[340px] h-[44px] border border-gray-200 rounded bg-white shadow-sm">
          <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          <span className="text-sm text-gray-600 font-medium">Signing in with Google…</span>
        </div>
      )}
    </div>
  );
}
