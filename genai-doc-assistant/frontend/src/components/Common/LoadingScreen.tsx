export function LoadingScreen() {
  return (
    <div className="flex h-screen items-center justify-center flex-col gap-4" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-3 h-3 rounded-full agent-pulse"
            style={{ backgroundColor: 'var(--color-accent)', animationDelay: `${i * 0.3}s` }}
          />
        ))}
      </div>
      <h2 className="text-xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Waking up the server...
      </h2>
      <p className="text-sm max-w-md text-center" style={{ color: 'var(--color-text-secondary)' }}>
        Free hosting sleeps after 15 minutes of inactivity. This takes about 30-60 seconds.
      </p>
    </div>
  );
}
