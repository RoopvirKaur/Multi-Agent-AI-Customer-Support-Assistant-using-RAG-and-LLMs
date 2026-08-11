export default function RegisterPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-2xl p-8 space-y-6 border border-slate-700">
        <h1 className="text-2xl font-bold text-center">Create Account</h1>
        <p className="text-slate-400 text-center text-sm">Join TechMart Support</p>
        {/* Auth form — wired in Phase 3 */}
        <div className="space-y-4">
          <input
            id="register-name"
            type="text"
            placeholder="Full name"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-indigo-500"
          />
          <input
            id="register-email"
            type="email"
            placeholder="Email address"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-indigo-500"
          />
          <input
            id="register-password"
            type="password"
            placeholder="Password"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-indigo-500"
          />
          <button
            id="register-submit"
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-medium transition-colors"
          >
            Create Account
          </button>
        </div>
        <p className="text-center text-sm text-slate-400">
          Already have an account?{" "}
          <a href="/login" className="text-indigo-400 hover:text-indigo-300">
            Sign in
          </a>
        </p>
      </div>
    </main>
  );
}
