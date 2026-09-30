"use client";

type CrudActionsProps = {
  onEdit?: () => void;
  onDelete?: () => void;
  editLabel?: string;
  deleteLabel?: string;
  disabled?: boolean;
};

export function CrudActions({
  onEdit,
  onDelete,
  editLabel = "Modifier",
  deleteLabel = "Supprimer",
  disabled = false,
}: CrudActionsProps) {
  if (!onEdit && !onDelete) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {onEdit && (
        <button
          type="button"
          onClick={onEdit}
          disabled={disabled}
          className="rounded-md px-2.5 py-1 text-[13px] font-medium text-teal-600 transition hover:bg-teal-50 disabled:opacity-50"
        >
          ✏️ {editLabel}
        </button>
      )}
      {onDelete && (
        <button
          type="button"
          onClick={onDelete}
          disabled={disabled}
          className="rounded-md px-2.5 py-1 text-[13px] font-medium text-red-500 transition hover:bg-red-50 disabled:opacity-50"
        >
          🗑️ {deleteLabel}
        </button>
      )}
    </div>
  );
}
