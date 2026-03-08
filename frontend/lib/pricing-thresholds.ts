export const MIN_MARGIN_PERCENT = 5
export const MANUAL_APPROVAL_MIN_MARGIN_PERCENT = 8

export function marginToneClass(margin: number): string {
  if (margin < MIN_MARGIN_PERCENT) return "text-destructive"
  if (margin < MANUAL_APPROVAL_MIN_MARGIN_PERCENT) return "text-warning"
  return "text-success"
}
