const puppeteer = require('puppeteer');

async function run() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Replace with the actual login URL
    await page.goto('https://qa.energyprint.com/login');

    // Replace with actual credentials
    await page.type('input[name="user_session_base[email]"]', 'developercandidate@energyprint.com');
    await page.type('input[name="user_session_base[password]"]', 'Energy1234');

    // Submit the form
    await page.click('input[type="submit"]');
    await page.waitForNavigation();

    // Select all rows in the table body
    const rows = await page.$$('#main-content tbody tr');
    const accounts = [];

    for (const row of rows) {
        const acctNumber = await row.$eval('td:nth-child(1)', el => el.textContent);
        const viewLink = await row.$eval('td:nth-child(2) a', el => el.getAttribute('href'));
        accounts.push({ acctNumber, viewLink });
    }

    const baseUrl = "https://qa.energyprint.com";

    for (const { acctNumber, viewLink } of accounts) {
        const acctPage = await browser.newPage();
        await acctPage.goto(`${baseUrl}${viewLink}`);

        // Extract PDF links and their invoice dates
        const pdfLinks = await acctPage.$$('.bill-table tbody tr');
        for (const link of pdfLinks) {
            const invoiceDate = (await link.$eval('td:nth-child(1)', el => el.textContent)).trim().replace('/', '-');
            let pdfUrl = await link.$eval('a', el => el.getAttribute('href'));

            if (!pdfUrl.startsWith('http')) {
                pdfUrl = baseUrl + pdfUrl;
            }

            const fileName = `file_source_${acctNumber}_${invoiceDate}.pdf`;
            const response = await acctPage.goto(pdfUrl);
            const buffer = await response.buffer();
            require('fs').writeFileSync(fileName, buffer);

            // Close the current page
            await acctPage.close();
        }
    }

    await browser.close();
}

run();
