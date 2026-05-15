export default function Spinner() {
  return (
    <span className="spinner" role="status" aria-label="Loading">
      <span className="spinner-dot" />
      <span className="spinner-dot" />
      <span className="spinner-dot" />
    </span>
  );
}