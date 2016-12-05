require 'json'

accounts = JSON.parse(File.read('snapshot_balances.json'))
accounts_to_fund = []

sharedrop = []
total_fund = 0.0
sharedrop_balance = 4567635.0
sharedrop_balance_after_registration = sharedrop_balance - accounts.size * 5.0
only_registration = 0

sharedrop_amount_validation = 0.0
total_fund_after_registration = 0.0

accounts.each do |account|
  total_fund += account['balance']
end

class Float
  def floor2(exp = 0)
   multiplier = 10 ** exp
   ((self * multiplier).floor).to_f/multiplier.to_f
  end
end

accounts.each do |account|
  balance = account['balance'].to_f
  if sharedrop_balance * balance / total_fund > 5.0
    account_summary = {
      account: account['name'],
      amount: balance
    }
    accounts_to_fund << account_summary
  else
    only_registration += 1
  end
end

accounts_to_fund.each do |account|
  total_fund_after_registration += account[:amount]
end

accounts_to_fund.each do |account|
  weight = account[:amount]
  sharedrop_amount = ((sharedrop_balance_after_registration + accounts_to_fund.size * 5.0) * weight / total_fund_after_registration) - 5
  account_summary = {
    account: account[:account],
    amount: sharedrop_amount.floor2(1)
  }
  sharedrop_amount_validation += sharedrop_amount
  sharedrop << account_summary
end

File.open("sharedrop_balances.json","w") do |f|
  f.write(JSON.pretty_generate(sharedrop))
end

puts "Needs to fund accounts: " + (accounts.size - only_registration).to_s
puts "Don't need to fund accounts: " + only_registration.to_s
puts "Sharedrop's balance: " + sharedrop_balance_after_registration.to_s
puts "Sharedrop's amount validation: " + sharedrop_amount_validation.to_s
puts "Done"
