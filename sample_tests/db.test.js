const db = require('./db');

test('connects to database', () => {
    expect(db.connect()).toBe(true);
});

test('executes query', () => {
    const result = db.query('SELECT 1');
    expect(result).toEqual({ rows: 1 });
});
