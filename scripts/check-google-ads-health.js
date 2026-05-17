const { GoogleAdsApi } = require('google-ads-api');

const CUSTOMER_ID = process.env.TARGET_CUSTOMER_ID || '6329354566';

async function checkAccountHealth() {
  try {
    const client = new GoogleAdsApi({
      developer_token: process.env.GOOGLE_ADS_DEVELOPER_TOKEN,
      client_id: process.env.GOOGLE_ADS_CLIENT_ID || process.env.GOOGLE_CLIENT_ID,
      client_secret: process.env.GOOGLE_ADS_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET,
    });

    const customer = client.Customer({
      customer_id: CUSTOMER_ID,
      refresh_token: process.env.GOOGLE_ADS_REFRESH_TOKEN,
    });

    // If you use a manager account (MCC), set this env and it will be used.
    if (process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID) {
      customer.login_customer_id = process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID;
    }

    // Note: access_token is not required when refresh_token is provided.



    console.log('=== Google Ads Account Health Check ===');
    console.log('Customer ID:', CUSTOMER_ID);
    console.log('Client: Dental Artistry');
    console.log('');

    // 1. Get account info
    console.log('--- Account Information ---');
    const accountQuery = `
      SELECT
        customer.id,
        customer.descriptive_name,
        customer.currency_code,
        customer.time_zone,
        customer.auto_tagging_enabled,
        customer.tracking_url_template,
        customer.status
      FROM customer
      LIMIT 1
    `;
    
    const accountData = await customer.query(accountQuery);
    console.log('Account Data:', JSON.stringify(accountData, null, 2));

    // 2. Get campaigns
    console.log('\n--- Campaigns ---');
    const campaignQuery = `
      SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros,
        campaign.start_date,
        campaign.end_date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc,
        metrics.cost_per_conversion
      FROM campaign
      WHERE segments.date DURING LAST_30_DAYS
    `;
    
    const campaigns = await customer.query(campaignQuery);
    console.log('Campaigns Count:', campaigns.length);
    console.log('Campaigns:', JSON.stringify(campaigns, null, 2));

    // 3. Get ad groups
    console.log('\n--- Ad Groups ---');
    const adGroupQuery = `
      SELECT
        ad_group.id,
        ad_group.name,
        ad_group.status,
        ad_group.campaign,
        ad_group.type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
      FROM ad_group
      WHERE segments.date DURING LAST_30_DAYS
    `;
    
    const adGroups = await customer.query(adGroupQuery);
    console.log('Ad Groups Count:', adGroups.length);
    console.log('Ad Groups:', JSON.stringify(adGroups.slice(0, 5), null, 2));

    // 4. Get ads
    console.log('\n--- Ads ---');
    const adQuery = `
      SELECT
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.policy_summary.approval_status,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions
      FROM ad_group_ad
      WHERE ad_group_ad.status != 'REMOVED'
    `;
    
    const ads = await customer.query(adQuery);
    console.log('Ads Count:', ads.length);
    
    // 5. Get account-level metrics
    console.log('\n--- Account Level Metrics (Last 30 Days) ---');
    const metricsQuery = `
      SELECT
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc,
        metrics.cost_per_conversion,
        metrics.search_impression_share,
        metrics.search_top_impression_share,
        metrics.search_absolute_top_impression_share,
        metrics.search_click_share,
        metrics.search_budget_lost_impression_share,
        metrics.search_rank_lost_impression_share
      FROM customer
      WHERE segments.date DURING LAST_30_DAYS
    `;
    
    const metrics = await customer.query(metricsQuery);
    console.log('Metrics:', JSON.stringify(metrics, null, 2));

    // 6. Get keywords
    console.log('\n--- Keywords ---');
    const keywordQuery = `
      SELECT
        ad_group_criterion.criterion_id,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.status,
        ad_group_criterion.quality_info.quality_score,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
      FROM ad_group_criterion
      WHERE ad_group_criterion.type = 'KEYWORD'
        AND segments.date DURING LAST_30_DAYS
    `;
    
    const keywords = await customer.query(keywordQuery);
    console.log('Keywords Count:', keywords.length);
    console.log('Keywords Sample:', JSON.stringify(keywords.slice(0, 5), null, 2));

  } catch (error) {
    console.error('Error message:', error && error.message);
    console.error('Error name:', error && error.name);
    console.error('Error stack:', error && error.stack);
    console.error('Raw error:', error);
    if (error && error.response) {
      console.error('Response:', JSON.stringify(error.response, null, 2));
    }
    process.exit(1);
  }
}

checkAccountHealth();
