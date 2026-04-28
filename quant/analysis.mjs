// Quick A-share market analysis
import { qverisFetch } from './qveris_fetch.mjs';

async function main() {
    console.log('=== 获取今日市场数据 ===\n');
    
    // Market overview
    try {
        const result = await qverisFetch('gildata_stock_market_overview.v1', {});
        console.log('市场概览:', JSON.stringify(result, null, 2));
    } catch(e) {
        console.log('市场概览失败:', e.message);
    }
    
    // Check our stock pool
    const stocks = [
        {code: '002594', name: '比亚迪'},
        {code: '300750', name: '宁德时代'},
        {code: '688114', name: '华大智造'},
        {code: '000762', name: '西藏矿业'},
        {code: '688487', name: '索辰科技'},
        {code: '603773', name: '沃格光电'},
        {code: '600552', name: '凯盛科技'},
        {code: '601020', name: '华钰矿业'},
        {code: '601318', name: '中国平安'},
        {code: '002415', name: '海康威视'},
    ];
    
    console.log('\n=== 持仓股票行情 ===\n');
    for (const s of stocks) {
        try {
            const r = await qverisFetch('gildata_asharelivequote.v1', {query: s.name + ' ' + s.code});
            if (r && r.data) {
                const d = r.data;
                console.log(`${s.name}(${s.code}): 现价=${d.price || d.close || 'N/A'} 涨跌=${d.change || d.pct_change || 'N/A'}% 量=${d.volume || 'N/A'}`);
            }
        } catch(e) {
            console.log(`${s.name}: 查询失败`);
        }
        await new Promise(r => setTimeout(r, 200));
    }
}

main().catch(console.error);
