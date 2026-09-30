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
          className="text-sm font-medium text-teal-700 hover:underline disabled:opacity-50"
        >
          {editLabel}
        </button>
      )}
      {onDelete && (
        <button
          type="button"
          onClick={onDelete}
          disabled={disabled}
          className="text-sm font-medium text-red-600 hover:underline disabled:opacity-50"
        >
          {deleteLabel}
        </button>
      )}
    </div>
  );
}
