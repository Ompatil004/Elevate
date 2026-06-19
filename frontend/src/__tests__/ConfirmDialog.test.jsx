/**
 * BUG-C2: Frontend component tests — ConfirmDialog
 * Verifies rendering, user interactions, and scroll-lock side effect.
 *
 * Run: npm run test:unit
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ConfirmDialog from '../components/ConfirmDialog';

describe('ConfirmDialog', () => {
  beforeEach(() => {
    document.body.style.overflow = '';
  });

  it('renders nothing when show=false', () => {
    const { container } = render(
      <ConfirmDialog show={false} message="Are you sure?" onConfirm={() => {}} onCancel={() => {}} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders the message and buttons when show=true', () => {
    render(
      <ConfirmDialog show={true} message="Delete this item?" onConfirm={() => {}} onCancel={() => {}} />
    );
    expect(screen.getByText('Delete this item?')).toBeInTheDocument();
    expect(screen.getByText('Confirm')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onConfirm with true when Confirm button is clicked', () => {
    const onConfirm = vi.fn();
    render(
      <ConfirmDialog show={true} message="Continue?" onConfirm={onConfirm} onCancel={() => {}} />
    );
    fireEvent.click(screen.getByText('Confirm'));
    expect(onConfirm).toHaveBeenCalledWith(true);
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel with false when Cancel button is clicked', () => {
    const onCancel = vi.fn();
    render(
      <ConfirmDialog show={true} message="Continue?" onConfirm={() => {}} onCancel={onCancel} />
    );
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledWith(false);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when backdrop is clicked', () => {
    const onCancel = vi.fn();
    const { container } = render(
      <ConfirmDialog show={true} message="Close me" onConfirm={() => {}} onCancel={onCancel} />
    );
    // Click the backdrop (first child = .confirm-modal-backdrop)
    fireEvent.click(container.firstChild);
    expect(onCancel).toHaveBeenCalledWith(false);
  });

  it('locks body scroll when shown', () => {
    render(
      <ConfirmDialog show={true} message="test" onConfirm={() => {}} onCancel={() => {}} />
    );
    expect(document.body.style.overflow).toBe('hidden');
  });

  it('restores body scroll when unmounted', () => {
    const { unmount } = render(
      <ConfirmDialog show={true} message="test" onConfirm={() => {}} onCancel={() => {}} />
    );
    unmount();
    expect(document.body.style.overflow).toBe('');
  });
});
