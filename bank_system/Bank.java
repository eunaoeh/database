package bank;

import java.sql.*;
import java.util.*;

public class Bank {
	private final static String driver = "com.mysql.cj.jdbc.Driver";
	private final static String url = "jdbc:mysql://localhost:3306/bank?serverTimezone=UTC";
	private final static String userID = "root";
	private final static String pw = "2017030482";

	private static Connection conn = null;
	private static PreparedStatement pstmt = null;
	private static ResultSet rs = null;
	
	public static void main(String[] agrs) throws Exception {
		try {
			Class.forName(driver).newInstance();
			conn = DriverManager.getConnection(url, userID, pw);
			System.out.println("DB Connection Success\n\n");
		
			System.out.println("BANK APPLICATION" + "\n-----------------------------\n");
			MainScreen();
			conn.close();
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(conn != null)
					conn.close();
			} catch(SQLException ex) {
				ex.printStackTrace();
			}
		}
	}
	//screen
	public final static void MainScreen() throws Exception{
		System.out.println("0. Exit\n" + "1. User Screen\n" + "2. Manager Screen");
		System.out.print("Input: ");
		Scanner sc = new Scanner(System.in);
		int input = sc.nextInt();
		if(input == 0) {
			sc.close();
			System.exit(0);
		}
		else if(input == 1) {
			UserScreen();
		}
		else if(input == 2) {
			ManagerScreen();
		}
	}
	public final static void UserScreen() throws Exception{
		System.out.println("\n0. Return to previous screen\n" + "1. Register User\n" + 
	"2. View User List\n" + "3. View My Info\n" + 
	"4. Create a bank account\n" + "5. View My Account Info\n" + 
	"6. Deposit Money\n" + "7. Withdraw Money\n" + "8. Delete a User");
		System.out.print("Input: ");
		Scanner sc = new Scanner(System.in);
		int input = sc.nextInt();
		System.out.print("\n-----------------------------\n");
		if(input == 0)
			MainScreen();
		else if(input == 1) {
			String name, ssn, gender, Address;
			int age;
			
			System.out.print("Name: ");
			Scanner sc1 = new Scanner(System.in);
			name = sc1.nextLine();
			
			System.out.print("Age: ");
			Scanner sc2 = new Scanner(System.in);
			age = sc2.nextInt();
			
			System.out.print("SSN: ");
			Scanner sc3 = new Scanner(System.in);
			ssn = sc3.nextLine();
			
			System.out.print("Gender: ");
			Scanner sc4 = new Scanner(System.in);
			gender = sc4.nextLine();
			
			System.out.print("Address: ");
			Scanner sc5 = new Scanner(System.in);
			Address = sc5.nextLine();
			
			insertUser(name,age,ssn,gender,Address);
			System.out.println("New User Registered\n");
		}
		else if(input == 2) {
			showUserList();
			UserScreen();
		}
		//show my info
		else if(input == 3) {
			System.out.print("Enter User SSN: ");
			Scanner sc1 = new Scanner(System.in);
			String ssn = sc1.nextLine();
			showUserInfo(ssn);
			UserScreen();
		}
		//create account
		else if(input == 4) {
			int money = 0;
			String name, ssn;
			
			Scanner sc1 = new Scanner(System.in);
			System.out.print("Enter account number(must be 5 numbers): ");
			name = sc1.nextLine();
			
			Scanner sc2 = new Scanner(System.in);
			System.out.print("Enter User SSN: ");
			ssn = sc2.nextLine();
			
			createAccount(money,name,ssn);
			UserScreen();
		}
		//check account
		else if(input == 5) {
			String ssn, accountnumber;
			
			Scanner sc1 = new Scanner(System.in);
			System.out.print("Enter Account Number: ");
			accountnumber = sc1.nextLine();
			
			Scanner sc2 = new Scanner(System.in);
			System.out.print("Enter User SSN: ");
			ssn = sc2.nextLine();
			
			myAccount(ssn, accountnumber);
			UserScreen();
		}
		//deposit
		else if(input == 6) {
			System.out.print("Enter User Account Number: ");
			Scanner sc1 = new Scanner(System.in);
			String accountnumber = sc1.nextLine();
			depositMoney(accountnumber);
			UserScreen();
		}
		//withdraw
		else if(input == 7) {
			System.out.print("Enter User Account Number: ");
			Scanner sc1 = new Scanner(System.in);
			String accountnumber = sc1.nextLine();
			withdrawMoney(accountnumber);
			UserScreen();
		}
		//delete
		else if(input == 8) {
			String answer = null;
			System.out.print("Did you create an account?(Y/N): ");
			Scanner sc1 = new Scanner(System.in);
			answer = sc1.nextLine();
			if(answer.equals("Y")) {
				String ssn = null;
				System.out.print("Enter your ssn: ");
				Scanner sc2 = new Scanner(System.in);
				ssn = sc2.nextLine();
				deleteAccount(ssn);
				deleteUser(ssn);
			}
			else if(answer.equals("N")) {
				String ssn = null;
				System.out.print("Enter your ssn: ");
				Scanner sc2 = new Scanner(System.in);
				ssn = sc2.nextLine();
				deleteUser(ssn);
			}
			UserScreen();
		}
		UserScreen();
		
	}
	public final static void ManagerScreen() throws Exception{
		System.out.println("\n0. Return to previous screen\n" + "1. Register Manager\n" + 
	"2. View Manager List\n" + "3. Delete a Manager");
		System.out.print("Input: ");
		Scanner sc = new Scanner(System.in);
		int input = sc.nextInt();
		System.out.print("\n-----------------------------\n");
		if(input == 0)
			MainScreen();
		else if(input == 1) {
			String name, ssn, gender, Address;
			int age;
			
			System.out.print("Name: ");
			Scanner sc1 = new Scanner(System.in);
			name = sc1.nextLine();
			
			System.out.print("Age: ");
			Scanner sc2 = new Scanner(System.in);
			age = sc2.nextInt();
			
			System.out.print("SSN: ");
			Scanner sc3 = new Scanner(System.in);
			ssn = sc3.nextLine();
			
			System.out.print("Gender: ");
			Scanner sc4 = new Scanner(System.in);
			gender = sc4.nextLine();
			
			System.out.print("Address: ");
			Scanner sc5 = new Scanner(System.in);
			Address = sc5.nextLine();
			
			insertManager(name,age,ssn,gender,Address);
			System.out.println("New Manager Registered\n");
			ManagerScreen();
		}
		else if(input == 2) {
			showMangerList();
			ManagerScreen();
		}
		else if(input == 3) {
			String ssn;
			System.out.print("Enter Manager SSN: ");
			Scanner sc1 = new Scanner(System.in);
			ssn = sc1.nextLine();
			
			deleteManager(ssn);
			ManagerScreen();
		}
		sc.close();
	}
	//insert User
	public static void insertUser(String name, int age, String ssn, String gender, String Address) {
		String sql = "INSERT INTO USER VALUES (?,?,?,?,?)";
		try {
			Class.forName(driver).newInstance();
			conn = DriverManager.getConnection(url,userID,pw);
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, name);
			pstmt.setInt(2, age);
			pstmt.setString(3, ssn);
			pstmt.setString(4, gender);
			pstmt.setString(5, Address);
			int cnt = pstmt.executeUpdate();
			if(cnt == 0)
				System.out.println("Failed to update date\n");
			
		}catch(SQLException | ClassNotFoundException | InstantiationException | IllegalAccessException e) {
			e.printStackTrace();
		}finally {
			try {
				if(pstmt != null && !pstmt.isClosed()) {
					pstmt.close();
				}
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//insert Manager
	public static void insertManager(String name, int age, String ssn, String gender, String Address) {
		String sql = "INSERT INTO MANAGER VALUES(?,?,?,?,?)";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, name);
			pstmt.setInt(2, age);
			pstmt.setString(3, ssn);
			pstmt.setString(4, gender);
			pstmt.setString(5, Address);
			int cnt = pstmt.executeUpdate();
			if(cnt == 0)
				System.out.println("Failed to update data\n");
			
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(pstmt != null && !pstmt.isClosed()) {
					pstmt.close();
				}
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//insert Account
	public static void createAccount(int money, String accountnumber, String userSSN) {
		String sql = "INSERT INTO ACCOUNT VALUES (?,?,?)";
		try {
			Class.forName(driver);
			conn = DriverManager.getConnection(url,userID,pw);
			pstmt = conn.prepareStatement(sql);
			pstmt.setInt(1, money);
			pstmt.setString(2, accountnumber);
			pstmt.setString(3, userSSN);
			int cnt = pstmt.executeUpdate();
			if(cnt == 0)
				System.out.println("Failed to create account\n");
			else
				System.out.println("Success to create account\n");
		} catch(SQLException | ClassNotFoundException e) {
			e.printStackTrace();
		}finally {
			try {
				if(pstmt != null && !pstmt.isClosed()) {
					pstmt.close();
				}
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//see my account
	public static void myAccount(String userSSN, String accountnumber) {
		String sql = "SELECT * from account where userSSN = ? and accountNumber = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, userSSN);
			pstmt.setString(2, accountnumber);
			rs = pstmt.executeQuery();
			while(rs.next()) {
				System.out.print("\n-----------------------------\n");
				int money = rs.getInt("money");
				String accountNumber = rs.getString("accountNumber");
				String ssn = rs.getString("userSSN");
				System.out.print("Money: " + money + "\nAccount Number: " + accountNumber + "\nUser ssn: " + userSSN
						+"\n-----------------------------\n");
			}
			rs.close();
			pstmt.close();
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(pstmt != null)
					pstmt.close();
			} catch(SQLException ex) {
				ex.printStackTrace();
			}
		}
		
	}
	//update - deposit money
	public static void depositMoney(String accountnumber) {
		System.out.print("Enter the amount money you deposit: ");
		Scanner sc1 = new Scanner(System.in);
		String amount = sc1.nextLine();
		String sql = "UPDATE account set money = money + ? where accountNumber = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, amount);
			pstmt.setString(2, accountnumber);
			int check = pstmt.executeUpdate();
			
			if(check == 0)
				System.out.println("\nFailed to depoit money");
			else if(check == 1)
				System.out.println("\nSuccess to deposit money");
			pstmt.close();
		} catch(SQLException e) {
			e.printStackTrace();
		} finally {
			try {
				if(pstmt != null && !pstmt.isClosed())
					pstmt.close();
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//withdraw money
	public static void withdrawMoney(String accountnumber) {
		System.out.print("Enter the amount money you withdraw: ");
		Scanner sc1 = new Scanner(System.in);
		String amount = sc1.nextLine();
		String sql = "UPDATE account set money = money - ? where accountNumber = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, amount);
			pstmt.setString(2, accountnumber);
			int check = pstmt.executeUpdate();
			
			if(check == 0)
				System.out.println("\nFailed to withdraw money");
			else if(check == 1)
				System.out.println("\nSuccess to withdraw money");
			pstmt.close();
		} catch(SQLException e) {
			e.printStackTrace();
		} finally {
			try {
				if(pstmt != null && !pstmt.isClosed())
					pstmt.close();
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//select one
	public static void showUserInfo(String Ssn) {
		String sql = "SELECT * from user where ssn = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, Ssn);
			rs = pstmt.executeQuery();
			while(rs.next()) {
				System.out.print("User Information\n-----------------------------\n");
				String name = rs.getString("name");
				String age = rs.getString("age");
				String ssn = rs.getString("ssn");
				String gender = rs.getString("gender");
				String Address = rs.getString("Address");
				System.out.print("NAME: " + name + "\nAGE: " + age + "\nSSN: " + ssn
						+ "\nGENDER: " + gender + "\nADDRESS: " + Address
						+ "\n-----------------------------\n");
			}
			rs.close();
			pstmt.close();
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(pstmt != null)
					pstmt.close();
			} catch(SQLException ex) {
				ex.printStackTrace();
			}
		}
	}
	//select * from user
	public static void showUserList() {
		Statement st = null;
		try {
			st = conn.createStatement();
			String sql = "SELECT * FROM USER";
			rs = st.executeQuery(sql);
			System.out.println("User List\n-----------------------------\n");
			while(rs.next()) {
				String name = rs.getString("name");
				String age = rs.getString("age");
				String ssn = rs.getString("ssn");
				String gender = rs.getString("gender");
				String Address = rs.getString("Address");
				System.out.print("NAME: " + name + "\nAGE: " + age + "\nSSN: " + ssn
						+ "\nGENDER: " + gender + "\nADDRESS: " + Address
						+ "\n-----------------------------\n");
			}
			rs.close();
			st.close();
			
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(st != null)
					st.close();
			} catch(SQLException ex) {
				ex.printStackTrace();
			}
		}
	}
	//show manager list
	public static void showMangerList() {
		Statement st = null;
		try {
			st = conn.createStatement();
			String sql = "SELECT * FROM MANAGER";
			rs = st.executeQuery(sql);
			System.out.println("Manager List\n-----------------------------\n");
			while(rs.next()) {
				String name = rs.getString("name");
				String age = rs.getString("age");
				String ssn = rs.getString("ssn");
				String gender = rs.getString("gender");
				String Address = rs.getString("Address");
				System.out.print("NAME: " + name + "\nAGE: " + age + "\nSSN: " + ssn
						+ "\nGENDER: " + gender + "\nADDRESS: " + Address
						+ "\n-----------------------------\n");
			}
			rs.close();
			st.close();
			
		} catch(Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(st != null)
					st.close();
			} catch(SQLException ex) {
				ex.printStackTrace();
			}
		}
	}
	//delete user
	public static void deleteUser(String ssn) {
		String sql = "DELETE FROM USER WHERE ssn = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, ssn);
			pstmt.executeUpdate();
			System.out.print("Success to delete user info\n");
		} catch(SQLException e) {
			e.printStackTrace();
		} finally {
			try {
				if(pstmt != null && !pstmt.isClosed())
					pstmt.close();
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//delete account
	public static void deleteAccount(String ssn) {
		String sql = "DELETE FROM ACCOUNT WHERE userSSN = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, ssn);
			pstmt.executeUpdate();
			System.out.println("Success to delete user account\n");
		} catch(SQLException e) {
			e.printStackTrace();
		} finally {
			try {
				if(pstmt != null && !pstmt.isClosed())
					pstmt.close();
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	//delete manager
	public static void deleteManager(String ssn) {
		String sql = "DELETE FROM MANAGER WHERE ssn = ?";
		try {
			pstmt = conn.prepareStatement(sql);
			pstmt.setString(1, ssn);
			pstmt.executeUpdate();
			System.out.println("Success to delete manager info\n");
		} catch(SQLException e) {
			e.printStackTrace();
		} finally {
			try {
				if(pstmt != null && !pstmt.isClosed())
					pstmt.close();
			} catch(SQLException e) {
				e.printStackTrace();
			}
		}
	}
	
}
