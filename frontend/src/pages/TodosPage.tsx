import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { Todo } from '../types';
import Spinner from '../components/Spinner';

export default function TodosPage() {
  const { username, logout } = useAuth();
  const navigate = useNavigate();

  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTitle, setNewTitle] = useState('');
  const [loadingTodos, setLoadingTodos] = useState(true);
  const [addingTodo, setAddingTodo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Verify token via /protected, then load todos
  useEffect(() => {
    let cancelled = false;
    const init = async () => {
      try {
        await api.get('/protected');
        const res = await api.get<Todo[]>('/todos');
        if (!cancelled) setTodos(res.data);
      } catch {
        if (!cancelled) {
          logout();
          navigate('/login');
        }
      } finally {
        if (!cancelled) setLoadingTodos(false);
      }
    };
    init();
    return () => { cancelled = true; };
  }, [logout, navigate]);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setError(null);
    setAddingTodo(true);
    try {
      const res = await api.post<Todo>('/todos', { title: newTitle.trim() });
      setTodos((prev) => [res.data, ...prev]);
      setNewTitle('');
    } catch {
      setError('Could not add todo. Please try again.');
    } finally {
      setAddingTodo(false);
    }
  };

  const handleToggle = async (todo: Todo) => {
    try {
      const res = await api.patch<Todo>(`/todos/${todo.id}`, { completed: !todo.completed });
      setTodos((prev) => prev.map((t) => (t.id === todo.id ? res.data : t)));
    } catch {
      setError('Could not update todo.');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/todos/${id}`);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch {
      setError('Could not delete todo.');
    }
  };

  const startEdit = (todo: Todo) => {
    setEditId(todo.id);
    setEditTitle(todo.title);
  };

  const saveEdit = async (id: string) => {
    if (!editTitle.trim()) return;
    try {
      const res = await api.patch<Todo>(`/todos/${id}`, { title: editTitle.trim() });
      setTodos((prev) => prev.map((t) => (t.id === id ? res.data : t)));
    } catch {
      setError('Could not save edit.');
    } finally {
      setEditId(null);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const done = todos.filter((t) => t.completed).length;

  return (
    <div className="todos-page">
      <header className="todos-header">
        <div className="todos-header-left">
          <span className="todos-logo">✦</span>
          <div>
            <h1 className="todos-title">My Tasks</h1>
            <p className="todos-meta">
              {username} · {done}/{todos.length} complete
            </p>
          </div>
        </div>
        <button className="btn-logout" onClick={handleLogout}>
          Sign out
        </button>
      </header>

      {error && (
        <div className="alert alert-error alert-inline">
          {error}
          <button onClick={() => setError(null)} className="alert-close">×</button>
        </div>
      )}

      <form onSubmit={handleAdd} className="add-form">
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="Add a new task…"
          className="add-input"
          disabled={addingTodo}
        />
        <button type="submit" className="btn-add" disabled={addingTodo || !newTitle.trim()}>
          {addingTodo ? <Spinner /> : '＋ Add'}
        </button>
      </form>

      {loadingTodos ? (
        <div className="todos-loading"><Spinner /></div>
      ) : todos.length === 0 ? (
        <div className="todos-empty">
          <span className="empty-icon">📋</span>
          <p>No tasks yet. Add one above!</p>
        </div>
      ) : (
        <ul className="todo-list">
          {todos.map((todo) => (
            <li key={todo.id} className={`todo-item ${todo.completed ? 'todo-done' : ''}`}>
              <button
                className="todo-check"
                onClick={() => handleToggle(todo)}
                aria-label={todo.completed ? 'Mark incomplete' : 'Mark complete'}
              >
                {todo.completed ? '✓' : ''}
              </button>

              {editId === todo.id ? (
                <input
                  className="todo-edit-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => saveEdit(todo.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') saveEdit(todo.id);
                    if (e.key === 'Escape') setEditId(null);
                  }}
                  autoFocus
                />
              ) : (
                <span className="todo-text" onDoubleClick={() => startEdit(todo)}>
                  {todo.title}
                </span>
              )}

              <div className="todo-actions">
                <button
                  className="btn-icon"
                  onClick={() => startEdit(todo)}
                  aria-label="Edit"
                  title="Edit (or double-click text)"
                >
                  ✎
                </button>
                <button
                  className="btn-icon btn-delete"
                  onClick={() => handleDelete(todo.id)}
                  aria-label="Delete"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {todos.length > 0 && done > 0 && (
        <div className="todos-footer">
          <button
            className="btn-clear"
            onClick={() =>
              todos
                .filter((t) => t.completed)
                .forEach((t) => handleDelete(t.id))
            }
          >
            Clear {done} completed
          </button>
        </div>
      )}
    </div>
  );
}