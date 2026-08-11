export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-2xl p-8 space-y-6 border border-slate-700">
        <h1 className="text-2xl font-bold text-center">Welcome Back</h1>
        <p className="text-slate-400 text-center text-sm">Sign in to TechMart Support</p>
        {/* Auth form — wired in Phase 3 */}
        <div className="space-y-4">
          <input
            id="login-email"
            type="email"
            placeholder="Email address"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-indigo-500"
          />
          <input
            id="login-password"
            type="password"
            placeholder="Password"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-indigo-500"
          />
          <button
            id="login-submit"
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-medium transition-colors"
          >
            Sign In
          </button>
        </div>
        <p className="text-center text-sm text-slate-400">
          Don&apos;t have an account?{" "}
          <a href="/register" className="text-indigo-400 hover:text-indigo-300">
            Register
          </a>
        </p>
      </div>
    </main>
  );
}
