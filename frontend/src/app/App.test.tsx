import { render, screen } from '@testing-library/react';

import { App } from './App';

describe('App', () => {
  it('muestra el nombre de la aplicación y el aviso legal', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'trAIde' })).toBeInTheDocument();
    expect(screen.getByRole('note')).toHaveTextContent(
      'Las señales son orientativas y no constituyen asesoramiento financiero',
    );
  });
});
