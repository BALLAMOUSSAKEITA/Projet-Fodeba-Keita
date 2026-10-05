"use client";

import { IconActionButton } from "@/components/ui/IconAction";

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
    <div className="flex items-center gap-1">
      {onEdit && (
        <IconActionButton
          label={editLabel}
          variant="neutral"
          icon="edit"
          disabled={disabled}
          onClick={onEdit}
        />
      )}
      {onDelete && (
        <IconActionButton
          label={deleteLabel}
          variant="danger"
          icon="trash"
          disabled={disabled}
          onClick={onDelete}
        />
      )}
    </div>
  );
}
