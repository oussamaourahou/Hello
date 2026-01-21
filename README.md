# Keja Conciergerie

Premium short-term rental management website for Nairobi property owners.

## Features

- **Modern Design**: Clean, professional design inspired by leading property management platforms
- **Fully Responsive**: Optimized for desktop, tablet, and mobile devices
- **Interactive UI**: FAQ accordion, smooth scrolling, form validation
- **Revenue Estimate Form**: Lead capture form for potential property owners
- **Trust Indicators**: Testimonials, case studies, and proof points

## Site Structure

- **Home**: Hero section with main CTA, proof points, how it works
- **Services**: Listing setup, pricing & revenue, guest experience, cleaning, maintenance, restocking
- **For Owners**: Target audience cards, responsibility comparison table, reporting preview
- **Pricing**: 3-tier pricing (Essential, Plus, Premium) with pass-through costs
- **About**: Company values and trust badges
- **FAQ**: Accordion-style frequently asked questions
- **Contact**: Revenue estimate form and WhatsApp integration

## Tech Stack

- **HTML5**: Semantic, accessible markup
- **CSS3**: Custom properties, Flexbox, Grid, responsive design
- **JavaScript**: Vanilla JS for interactivity (no dependencies)
- **Fonts**: Inter from Google Fonts

## Getting Started

1. Open the frontend folder:
```bash
cd frontend
```

2. Serve with a simple HTTP server:
```bash
# Python 3
python -m http.server 8080

# Or Node.js (if http-server is installed)
npx http-server -p 8080
```

3. Open in browser: `http://localhost:8080`

## Customization

### Update Contact Information
Edit `index.html` to replace placeholder contact details:
- WhatsApp number: Search for `254700000000` and replace with your actual number
- Email: Search for `hello@kejaconciergerie.com` and replace

### Update Colors
Edit `style.css` CSS variables at the top of the file:
```css
:root {
    --color-primary: #0F4C81;
    --color-accent: #E85D04;
    /* ... */
}
```

### Add Real Images
Replace the hero placeholder with actual property images by adding an `<img>` tag or background image.

## Form Integration

The revenue estimate form currently logs to console. To connect to a backend:

1. Update the form submission handler in `app.js`
2. Replace the simulated API call with your actual endpoint
3. Example with fetch:
```javascript
const response = await fetch('/api/leads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
});
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

All rights reserved. Keja Conciergerie 2025.
