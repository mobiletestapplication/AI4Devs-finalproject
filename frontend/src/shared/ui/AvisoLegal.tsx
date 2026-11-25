export const TEXTO_AVISO_LEGAL =
  'Las señales son orientativas y no constituyen asesoramiento financiero';

export function AvisoLegal() {
  return <p role="note">{TEXTO_AVISO_LEGAL}</p>;
}
